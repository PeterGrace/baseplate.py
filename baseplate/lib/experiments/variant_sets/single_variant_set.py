from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from baseplate.lib.experiments.variant_sets.base import VariantSet


class SingleVariantSet(VariantSet):
    """Variant Set designed to handle two total treatments.

    This VariantSet allows adjusting the sizes of variants without
    changing treatments, where possible. When not possible (eg:
    switching from a 60/40 distribution to a 40/60 distribution),
    this will minimize changing treatments (in the above case, only
    those buckets between the 40th and 60th percentile of the bucketing
    range will see a change in treatment).

    :param variants: array of dicts, each containing the keys 'name'
        and 'size'. Name is the variant name, and size is the fraction of
        users to bucket into the corresponding variant. Sizes are expressed
        as a floating point value between 0 and 1.
    :param num_buckets: the number of potential buckets that can be
        passed in for a variant call. Defaults to 1000, which means maximum
        granularity of 0.1% for bucketing

    """

    # pylint: disable=super-init-not-called
    def __init__(self, variants: List[Dict[str, Any]], num_buckets: int = 1000):
        self.variants = variants
        self.num_buckets = num_buckets

        self._validate_variants()

    def __contains__(self, item: str) -> bool:
        if self.variants[0].get("name") == item or self.variants[1].get("name") == item:
            return True

        return False

    def _validate_variants(self) -> None:
        if self.variants is None:
            raise ValueError("No variants provided")

        if len(self.variants) != 2:
            raise ValueError("Single Variant experiments expect only one variant and one control.")

        if self.variants[0].get("size") is None or self.variants[1].get("size") is None:
            raise ValueError(f"Variant size not provided: {self.variants}")

        total_size = self.variants[0]["size"] + self.variants[1]["size"]

        if total_size < 0.0 or total_size > 1.0:
            raise ValueError("Sum of all variants must be between 0 and 1.")

    def choose_variant(self, bucket: int) -> Optional[str]:
        """Deterministically choose a variant.

        Every call with the same bucket on one instance will result in the same
        answer

        :param bucket: an integer bucket representation
        :return: the variant name, or None if bucket doesn't fall into any of the variants
        """
        if bucket < int(self.variants[0]["size"] * self.num_buckets):
            return self.variants[0]["name"]

        if bucket >= self.num_buckets - int(self.variants[1]["size"] * self.num_buckets):
            return self.variants[1]["name"]

        return None

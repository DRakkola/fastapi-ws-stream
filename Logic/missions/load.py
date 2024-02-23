from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import delegations

delegations_mapping = {
    "id_del": "id",
    "del_fr": "del_fr",
    "del_ar": "del_ar",
    "gouv_id": "gouv_id",
    "gouv_fr": "gouv_fr",
    "gouv_ar": "gouv_ar",
    "geometry": "MULTIPOLYGON",
}

delegations_shp = Path(__file__).resolve().parent / "data" / "delegations.shp"


def run(verbose=True):
    lm = LayerMapping(delegations, delegations_shp, delegations_mapping, transform=False)
    lm.save(strict=True, verbose=verbose)
import random
from typing import Any

from fastapi import APIRouter

from py_challenge_data_service import logger
from py_challenge_data_service.models import (
    AnimalCharacteristics,
    AnimalClassification,
    RequestInput,
)

router = APIRouter(
    tags=["animals"],
)


@router.get(
    "/schema",
    summary="Get the schema of the data",
    description="This endpoint returns the schema of the animal data provided by this service.",
)
async def get_schema() -> dict[str, Any]:
    return AnimalCharacteristics.model_json_schema()


@router.post(
    "/data",
    summary="Get the data",
    description="This endpoint returns animal data.",
)
async def get_data(
    request: RequestInput,
) -> list[AnimalCharacteristics]:
    random.seed(request.seed)
    results = []
    for _ in range(request.number_of_datapoints):
        if random.random() < 0.05:
            # With a small, random chance we will return noise to generate outliers
            results.append(
                AnimalCharacteristics(
                    walks_on_n_legs=random.randint(1, 5),
                    height=random.uniform(0, 10),
                    weight=random.uniform(0, 1000),
                    has_wings=random.choice([True, False]),
                    has_tail=random.choice([True, False]),
                )
            )
            continue
        choosen_animal = random.choice(list(AnimalClassification.__members__.values()))
        match AnimalClassification(choosen_animal):
            case AnimalClassification.KANGAROO:
                # Source: https://en.wikipedia.org/wiki/Kangaroo
                results.append(
                    AnimalCharacteristics(
                        walks_on_n_legs=2,
                        height=random.uniform(1.6, 2),
                        weight=random.uniform(40, 90),
                        has_wings=False,
                        has_tail=True,
                    )
                )
            case AnimalClassification.ELEPHANT:
                # Source: https://en.wikipedia.org/wiki/Elephant
                results.append(
                    AnimalCharacteristics(
                        walks_on_n_legs=4,
                        height=random.uniform(2.47, 3.36),
                        weight=random.uniform(2600, 6900),
                        has_wings=False,
                        has_tail=True,
                    )
                )
            case AnimalClassification.CHICKEN:
                # Source: https://en.wikipedia.org/wiki/Chicken
                results.append(
                    AnimalCharacteristics(
                        walks_on_n_legs=2,
                        height=random.uniform(0.15, 0.50),
                        weight=random.uniform(0.037, 4.2),
                        has_wings=True,
                        has_tail=True,
                    )
                )
            case AnimalClassification.DOG:
                # Source: https://en.wikipedia.org/wiki/Dog
                results.append(
                    AnimalCharacteristics(
                        walks_on_n_legs=4,
                        height=random.uniform(0.13, 0.81),
                        weight=random.uniform(0.5, 79),
                        has_wings=False,
                        has_tail=True,
                    )
                )
            case _:
                assert False, "This should never happen. Maybe the enum was modified?"

    logger.info(
        "Sucessfully generated data",
        number_of_datapoints=request.number_of_datapoints,
        seed=request.seed,
    )

    return results

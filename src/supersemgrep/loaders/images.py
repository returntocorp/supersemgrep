import io
import json
from pathlib import Path
from . import base

from google.cloud import vision


class Loader(base.Loader):
    NEEDS = {
        base.Option(
            name="google_cloud_keyfile_path",
            instructions="Get a service account keyfile at https://cloud.google.com/vision/docs/libraries#setting_up_authentication",
            persist=True,
        ),
    }

    @staticmethod
    def get_objects(response):
        def get_box_area(box):
            top_left = box.bounding_poly.normalized_vertices[0]
            bottom_right = box.bounding_poly.normalized_vertices[2]
            return (bottom_right.x - top_left.x) * (bottom_right.y - top_left.y)

        def is_inside(big_box, small_box):
            if big_box.name == small_box.name:
                return False  # don't nest duplicate recognitions
            big_top_left = big_box.bounding_poly.normalized_vertices[0]
            big_bottom_right = big_box.bounding_poly.normalized_vertices[2]
            small_top_left = small_box.bounding_poly.normalized_vertices[0]
            small_bottom_right = small_box.bounding_poly.normalized_vertices[2]

            TOLERANCE = 0.05

            return (
                (big_top_left.x - small_top_left.x < TOLERANCE)
                and (big_top_left.y - small_top_left.y < TOLERANCE)
                and (small_bottom_right.x - big_bottom_right.x < TOLERANCE)
                and (small_bottom_right.y - big_bottom_right.y < TOLERANCE)
            )

        def process_box(box, remaining_boxes):
            this_object = {"name": box.name, "objects": [], "size": get_box_area(box)}
            for index, other_box in enumerate([*remaining_boxes]):
                if is_inside(box, other_box):
                    remaining_boxes.pop(index)
                    this_object["objects"].append(
                        process_box(other_box, remaining_boxes)
                    )
            return this_object

        annotations = sorted(
            response.localized_object_annotations,
            key=get_box_area,
            reverse=True,
        )
        objects = []
        while annotations:
            objects.append(process_box(annotations.pop(0), annotations))

        return objects

    def create_target(self, directory: Path) -> None:
        client = vision.ImageAnnotatorClient.from_service_account_file(
            self.options["google_cloud_keyfile_path"]
        )
        paths = Path("targets").glob("**/*.jpg")
        for path in paths:
            response = client.annotate_image(
                {
                    "image": {"content": path.read_bytes()},
                    "features": [
                        {"type_": "LANDMARK_DETECTION"},
                        {"type_": "LABEL_DETECTION"},
                        {"type_": "TEXT_DETECTION"},
                        {"type_": "IMAGE_PROPERTIES"},
                        {"type_": "OBJECT_LOCALIZATION"},
                    ],
                }
            )
            result = {
                "text": response.full_text_annotation.text,
                "colors": [
                    {
                        "red": color.color.red,
                        "green": color.color.green,
                        "blue": color.color.blue,
                    }
                    for color in response.image_properties_annotation.dominant_colors.colors
                    if color.score > 0.1
                ],
                "labels": [label.description for label in response.label_annotations],
                "landmarks": [
                    {
                        "name": landmark.description,
                        "lat": landmark.locations[0].lat_lng.latitude,
                        "lon": landmark.locations[0].lat_lng.longitude,
                    }
                    for landmark in response.landmark_annotations
                ],
                "objects": self.get_objects(response),
            }

            json_path = directory / f"{path.stem}-annotations.json"
            json_path.write_text(json.dumps(result, indent=2))

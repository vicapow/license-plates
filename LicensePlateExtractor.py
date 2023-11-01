import torch
import uuid
import re
from osx_ocr import osx_ocr
from PIL import Image
import shutil
import tempfile
from transformers import YolosFeatureExtractor, YolosForObjectDetection

LICENSE_DATA_PATH = "data/license_plates"
FRAME_DATA_PATH = "data/frames"

LICENSE_PLAET_PATTERN = r'^[A-Z0-9]+$'


class LicensePlateExtractor:
    def __init__(self, args):
        self.args = args
        # Reference usage: https://huggingface.co/spaces/nickmuchi/license-plate-detection-with-YOLOS/blob/main/app.py
        self._feature_extractor = YolosFeatureExtractor.from_pretrained(
            'nickmuchi/yolos-small-rego-plates-detection')
        self._model = YolosForObjectDetection.from_pretrained(
            'nickmuchi/yolos-small-rego-plates-detection')
        self._model = torch.compile(self._model)

    def extract(self, image):
        print('inputs')
        inputs = self._feature_extractor(images=image, return_tensors="pt")
        print('outputs')
        outputs = self._model(**inputs)
        print(f"image.size: {image.size}")
        img_size = torch.tensor(
            [tuple(reversed(image.size))])
        processed_outputs = self._feature_extractor.post_process(
            outputs, img_size)
        output_dict = processed_outputs[0]
        threshold = 0.8
        keep = output_dict["scores"] > threshold
        boxes = output_dict["boxes"][keep].tolist()
        scores = output_dict["scores"][keep].tolist()
        labels = output_dict["labels"][keep].tolist()
        id2label = self._model.config.id2label
        labels = [id2label[x] for x in labels]
        plates = []
        for index, (score, box, label) in enumerate(zip(scores, boxes, labels)):
            if label == 'license-plates':
                plate = image.copy()
                plate = plate.crop(box)
                plates.append(plate)
        return plates

    def extract_and_save(self, img):
        print('extract_and_save')
        plates = self.extract(img)
        print(f"num plates: {len(plates)}")
        for index, plate in enumerate(plates):
            with tempfile.NamedTemporaryFile(delete=False) as plate_file:
                file_path = plate_file.name
                plate.save(file_path, format="PNG")
                plate_text = osx_ocr(
                    file_path) if not self.args.skip_ocr else None
                if not re.match(LICENSE_PLAET_PATTERN, plate_text):
                    plate_text = None
                if plate_text is not None and plate_text != "":
                    dst_path = LICENSE_DATA_PATH + \
                        '/plate_' + plate_text + '.png'
                    shutil.move(file_path, dst_path)
                    print("plate_text: " + plate_text)
                else:
                    dst_path = LICENSE_DATA_PATH + \
                        '/plate_UNKNOWN_' + str(uuid.uuid4()) + '.png'
                    shutil.move(file_path, dst_path)
                    print('unable to read plate: ' + dst_path)

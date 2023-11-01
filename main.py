import os
import io
import requests
import cv2
import time
import asyncio
import aiohttp
from PIL import Image
from LicensePlateExtractor import LicensePlateExtractor, LICENSE_DATA_PATH, FRAME_DATA_PATH
import multiprocessing
from args import parse_args

LICENSE_DATA_PATH = "data/license_plates"
FRAME_DATA_PATH = "data/frames"


def mkdirp(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


mkdirp(LICENSE_DATA_PATH)
mkdirp(FRAME_DATA_PATH)


async def process_image_worker(session, images, host):
    while True:
        print('before images.get()')
        image = await images.get()
        print('process queue item')
        # Convert the image to bytes
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        url = f"http://{host}"
        print(f"requesting {url}")

        headers = {'Content-Type': 'image/jpeg'}

        async with session.post(url, data=image_bytes.getvalue(), headers=headers) as response:
            print('response')
            # print(f"response status: {response.status_code}")


async def main():
    args = parse_args()
    host_index = 0

    vid = cv2.VideoCapture(args.capture_id)

    plate_extractor = LicensePlateExtractor(
        args) if args.hosts and len(args.hosts) > 0 else None

    if args.debug_frame is not None and len(args.debug_frame):
        img = Image.open(args.debug_frame)
        plate_extractor.extract_and_save(img)
        return

    images = asyncio.Queue(maxsize=len(args.hosts)) if args.hosts and len(
        args.hosts) > 0 else None

    async with aiohttp.ClientSession() as session:
        workers = [asyncio.create_task(process_image_worker(session, images, args.hosts[index])) for index in range(
            len(args.hosts))] if args.hosts and len(args.hosts) else None
        try:
            while True:
                ret, frame = vid.read()
                if frame is None or frame.size == 0:
                    continue
                # Convert the BGR frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Create a PIL image from the NumPy array
                img = Image.fromarray(frame_rgb)

                if args.record_frames:
                    current_time_milliseconds = int(time.time() * 1000)
                    fame_path = f"{FRAME_DATA_PATH}/frame_{current_time_milliseconds}.jpg"
                    img.save(fame_path, FORMAT="JPEG")
                    print(f"frame: {fame_path}")
                if args.process_plates:
                    if args.hosts is not None and len(args.hosts) > 0:
                        await images.put(img)
                        print("add queue item")
                    else:
                        plate_extractor.extract_and_save(img)

        except KeyboardInterrupt:
            vid.release()
            print("\nProgram terminated by user.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

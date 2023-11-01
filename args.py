import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="License plate readinger")
    parser.add_argument('--port', type=int, default=8000,
                        help='Which port the server should run on ')
    parser.add_argument('--hosts', type=str,
                        help='Comma-separated list of host strings')
    parser.add_argument('--capture-id', type=int, default=0,
                        help='Pick the device id to capture from')
    parser.add_argument('--record-frames', action='store_true',
                        help='Should the process save webcam frames?')
    parser.add_argument('--process-plates', action="store_true",
                        help="Should we process the license plates from the frames?")
    parser.add_argument('--debug-frame', type=str,
                        help="Debug a single frame and then exist")
    parser.add_argument('--skip-ocr', action="store_true",
                        help="Skip running ocr")
    args = parser.parse_args()
    args.hosts = args.hosts.split(',') if args.hosts else None
    return args

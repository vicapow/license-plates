# An experiment to see if I can automatically detect stolen license plates

## To update requirements.txt

    conda list --export > requirements.txt

## To run the notebook

    jupyter notebook

# To run the servers that takes an image and produces the license plate

    python server.py --port=8001
    python server.py --port=8002

To run the process that reads from the webcam and passes it to the "worker" servers, you can do

    python main.py \
      --hosts=localhost:8001,localhost:8002 \
      --record-frames \ # save the frames to data/frames
      --process-plates  # pass the frames to the workers to try and detect and decode the license plates

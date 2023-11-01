import subprocess
import tempfile
import os

# Surprisingly, a lot of the OCR libraries I came across
# only worked well for like scanned documents, not for unusual
# photos, of stuff, like license plates. However, the built in
# OS X mechanism worked well. To use that, I first had to
# setup a "shortcut" using the shortcut app, called "ocr"
# that took an image as input and text output, then I was
# able to call that using the "shortcuts" command line
# utility and it worked OK.


def osx_ocr(input_path):
    # Create a temporary file for the output text
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as output_temp_file:
        output_path = output_temp_file.name

    # Construct the command
    command = [
        "shortcuts",
        "run",
        "ocr",
        "--input-path",
        input_path,
        "--output-type",
        "public.plain-text",
        "--output-path",
        output_path
    ]

    try:
        # Run the OCR command
        # print("COMMAND: " + " ".join(command))
        subprocess.run(command, check=True)

        # Read the result from the output file
        with open(output_path, 'r') as result_file:
            result_text = result_file.read()

        return result_text
    except subprocess.CalledProcessError as e:
        # Handle any errors from the command
        print(f"OCR command failed with error: {e}")
    finally:
        # Clean up the temporary files
        if output_path:
            os.remove(output_path)

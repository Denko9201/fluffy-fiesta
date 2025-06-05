import argparse
import subprocess
import os
import tempfile


def run_ffmpeg(input_path, output_path):
    """Run ffmpeg to convert between video containers."""
    cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
    subprocess.run(cmd, check=True)


def make_xmp(offset):
    """Return XMP packet for Android Motion Photo with given offset."""
    xml = f"""<?xpacket begin='\ufeff' id='W5M0MpCehiHzreSzNTczkc9d'>
<x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Python'>
 <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
  <rdf:Description xmlns:GCamera='http://ns.google.com/photos/1.0/camera/'
   GCamera:MicroVideo='1'
   GCamera:MicroVideoVersion='1'
   GCamera:MicroVideoOffset='{offset}'/>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'>"""
    return xml.encode("utf-8")


def ios_to_android(jpeg_path, mov_path, output_path):
    with tempfile.TemporaryDirectory() as tmp:
        mp4_path = os.path.join(tmp, "temp.mp4")
        run_ffmpeg(mov_path, mp4_path)

        with open(jpeg_path, "rb") as f:
            jpeg = f.read()
        with open(mp4_path, "rb") as f:
            mp4 = f.read()

        soi = jpeg[:2]
        rest = jpeg[2:]

        # initial xmp to determine length
        xmp = make_xmp(0)
        offset = len(soi) + 4 + len(xmp) + len(rest)
        xmp = make_xmp(offset)
        app1 = b"\xFF\xE1" + (len(xmp) + 2).to_bytes(2, "big") + xmp

        new_jpeg = soi + app1 + rest
        with open(output_path, "wb") as f:
            f.write(new_jpeg)
            f.write(mp4)


def android_to_ios(motion_photo_path, output_prefix):
    with tempfile.TemporaryDirectory() as tmp:
        with open(motion_photo_path, "rb") as f:
            data = f.read()

        eoi = data.rfind(b"\xFF\xD9")
        if eoi == -1:
            raise ValueError("Not a JPEG file")
        jpeg_data = data[:eoi + 2]
        mp4_data = data[eoi + 2 :]

        mp4_path = os.path.join(tmp, "temp.mp4")
        with open(mp4_path, "wb") as f:
            f.write(mp4_data)

        mov_path = output_prefix + ".mov"
        jpeg_out = output_prefix + ".jpg"

        run_ffmpeg(mp4_path, mov_path)
        with open(jpeg_out, "wb") as f:
            f.write(jpeg_data)


def main():
    parser = argparse.ArgumentParser(description="Convert between iOS Live Photos and Android Motion Photos")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("ios2android", help="Convert Live Photo to Motion Photo")
    p1.add_argument("jpeg")
    p1.add_argument("mov")
    p1.add_argument("output")

    p2 = sub.add_parser("android2ios", help="Convert Motion Photo to Live Photo")
    p2.add_argument("motion_photo")
    p2.add_argument("output_prefix")

    args = parser.parse_args()

    if args.cmd == "ios2android":
        ios_to_android(args.jpeg, args.mov, args.output)
    elif args.cmd == "android2ios":
        android_to_ios(args.motion_photo, args.output_prefix)


if __name__ == "__main__":
    main()

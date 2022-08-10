import os
import uuid
import pathlib

base_path = pathlib.Path(__file__).parent.absolute()

with open(base_path / "ids.txt", "w") as f:
    for i in os.listdir(base_path / "pics"):
        uid = uuid.uuid4().hex
        with open(os.path.join(base_path, "pics", i), "rb") as old:
            xold = old.read()
        with open(os.path.join(base_path, "new", str(uid) + ".png"), "wb") as new:
            new.write(xold)
        f.write(str(uid) + "\n")
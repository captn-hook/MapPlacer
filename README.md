# MapPlacer
Blender add-on for placing objects on a map.

[blender_manifest.toml](./blender_manifest.toml)

    blender --command extension build --split-platforms

create wheels:

    pip download pyproj --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=macosx_11_0_arm64
    pip download pyproj --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_28_x86_64
    pip download pyproj --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64


# notes
data only had 29 / 178 objects after removing duplicates


# unsure what to do about country level data- some DBs have a location, and several countries associated with it, some have no location, some have a location and no countries associated with it.

# what is single site
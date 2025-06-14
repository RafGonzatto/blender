# Blender Scene Setup

This repository contains a Python script to configure a Blender scene with professional lighting, camera placement, and render settings.

## Prerequisites
- Blender (4.x or newer)
- Git LFS to store `.blend` files efficiently

Install Blender using your package manager and enable Git LFS:

```bash
sudo apt-get install -y blender git-lfs
git lfs install
```

## Generating `projeto.blend`
1. Create or copy your initial `.blend` file into this directory and name it `projeto.blend`.
2. Run Blender in background mode with the setup script:

```bash
blender -b projeto.blend --python setup_scene.py
```

The script will:
- Remove existing lights
- Ensure a camera exists and points at the scene center
- Add three-point lighting
- Configure Cycles with GPU rendering, denoising, and 4K resolution
- Add subtle volume scattering
- Save the updated `.blend`

## Creating a Zip
If you need to share the file as a zip, run:

```bash
zip -9 projeto_blend.zip projeto.blend
```

The `.gitattributes` file already tracks `*.blend` with Git LFS so large files are handled efficiently. After generating the files, commit them with Git:

```bash
git add projeto.blend projeto_blend.zip
git commit -m "Add generated blend project"
```


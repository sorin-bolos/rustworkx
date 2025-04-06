from setuptools import setup, find_packages

setup(
    name="rustworkx",
    version="0.17.0",
    description="Python bindings for the rustworkx graph library (WebAssembly version)",
    author="Matthew Treinish",
    author_email="mtreinish@kortar.org",
    packages=find_packages(),
    package_data={
        "rustworkx": ["*.wasm", "*.js"],
    },
    python_requires=">=3.7",
)

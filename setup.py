from setuptools import setup, find_packages

setup(
    name="chemdiagrams",          
    version="0.1.0",             
    description="Energy diagram plotting package",
    author="Tim Bastian Enders",    
    packages=find_packages(),      
    python_requires=">=3.10",      
    install_requires=[
        "matplotlib>=3.7",        
    ],
    include_package_data=True,     
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
# 1. clone the repo
# 2. create the Dockerfile
# 3. replace the install.py with the one below (some of the install steps were moved to the Dockerfile, and some of the manual build steps were updated to use older versions of the dependencies)
# 4. create a file called sketch-frontend-pom.xml with the below contents (the sketch-frontend build was slow / broken, this file changes a few settings, the updated install.py will copy this file over before trying to build)
# with those 3 files updated / in place you can build / run and exec with docker (run the commands from within the cloned repo):

# 5. build the image
docker build -t icsg .
# 6. make a directory to store the results of the runs
mkdir results
# 7. run the container based on this image in the background with a volume pointed at the results directory
docker run -it -d --name icsg -v $(pwd)/results:/usr/src/results icsg /bin/bash
# 8. run an interactive shell on the running container
docker exec -it icsg /bin/bash
# 9. activate conda env
source $HOME/miniconda/bin/activate && conda activate inv_csg_env
# 10. run the code (the build folder is called build, manually point to the results folder we have mapped, see the run_tests.py file for more examples)
python3 main.py --builddir build --outdir ../results/one_cube --mesh example/one_cube/csg_low_res.off --eps 0.1 --surfacedensity 100 --volumedensity 10
# 11. view the results in the results folder
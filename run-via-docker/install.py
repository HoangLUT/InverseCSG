# this file was updated to use older versions of sketch frontend / backend
# also, apt and python dependency installs were moved into the Dockerfile

import os, sys, subprocess
import readline, glob # For autocompleting file path.
import urllib.request
import shutil
import helper
import argparse

HERE = os.path.abspath(os.path.dirname(__file__))

# Logics behind this script: it tries to check if all necessary dependences are
# installed. If any of them is missing, it will attempt to download and install
# them, which may require adding new environment variables. To avoid polluting
# users' environment variables, we will save them into an ENVIRONMENT file and
# load them at the beginning of our scripts.

################################################################################
# Helpers.
################################################################################

# Credit:
# https://stackoverflow.com/questions/6656819/filepath-autocompletion-using-users-input
def AutoComplete(text, state):
  return (glob.glob(text + '*') + [None])[state]

def SaveCustomizedEnvironmentVariables(env_variables, file_path):
  f = open(file_path, 'w')
  f.write('# You can manually change the environment variables below:\n')
  for key, val in env_variables.items():
    f.write('%s: %s\n' % (key, val))

def CheckVersionNumber(version_number, target):
  major, minor, change = version_number.split('.')
  major = int(major)
  minor = int(minor)
  change = int(change)
  target_major, target_minor, target_change = target.split('.')
  target_major = int(target_major)
  target_minor = int(target_minor)
  target_change = int(target_change)
  if major > target_major:
    return True
  if major < target_major:
    return False
  if minor > target_minor:
    return True
  if minor < target_minor:
    return False
  if change >= target_change:
    return True
  else:
    return False
  
def CheckSketch(build_folder):
  sketch_result = subprocess.getoutput('sketch')
  # The first line should be something like:
  # SKETCH version 1.7.4
  # The following is not a very robust way to check the version number.
  if 'SKETCH version' not in sketch_result:
    return False
  # Now check version number.
  first_line = sketch_result.splitlines()[0]
  _, _, version_number = first_line.strip().split()
  # Expect to see >= 1.7.4.
  if not CheckVersionNumber(version_number, '1.7.4'):
    return False
  # Now Sketch seems working.
  helper.PrintWithGreenColor('Sketch %s seems successfully installed.' %
                       version_number)
  # Save environment variables into files.
  sketch_loc = subprocess.getoutput('whereis sketch')
  env_variables['CSG_SKETCH'] = sketch_loc.strip().split()[1].strip()
  # Auto-complete paths.
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(AutoComplete)

  # try local first : build/sketch/sketch-frontend
  sketch_frontend_folder = os.path.join(build_folder, 'sketch', 'sketch-frontend')
  if os.path.exists(sketch_frontend_folder):
    env_variables['CSG_SKETCH_FRONTEND'] = sketch_frontend_folder
  sketch_backend_folder = os.path.join(build_folder, 'sketch', 'sketch-backend')
  if os.path.exists(sketch_backend_folder):
    env_variables['CSG_SKETCH_BACKEND'] = sketch_backend_folder

  err_cnt = 0
  while 'CSG_SKETCH_FRONTEND' not in env_variables:
    sketch_frontend_folder = input('Tell us the location of sketch-frontend: ') 
    if not os.path.exists(sketch_frontend_folder):
      print('Folder does not exist. Please try again.')
      err_cnt += 1
      continue
    env_variables['CSG_SKETCH_FRONTEND'] = sketch_frontend_folder
    if err_cnt > 5:
      print('CSG_SKETCH_FRONTEND not found in environment variables. Re-download.')
      return False

  err_cnt = 0
  while 'CSG_SKETCH_BACKEND' not in env_variables:
    sketch_backend_folder = input('Tell us the location of sketch-backend: ') 
    if not os.path.exists(sketch_backend_folder):
      print('Folder does not exist. Please try again.')
      err_cnt += 1
      continue
    env_variables['CSG_SKETCH_BACKEND'] = sketch_backend_folder
    if err_cnt > 5:
      print('CSG_SKETCH_BACKEND not found in environment variables. Re-download.')
      return False

  return True

def InstallCGAL(build_folder, init=True):
  if init:
    cgal_url = 'https://github.com/CGAL/cgal/releases/download/' \
               'releases%2FCGAL-4.12/CGAL-4.12.zip'
    cgal_file = os.path.join(build_folder, 'cgal.zip')
    urllib.request.urlretrieve(cgal_url, cgal_file)
    helper.Run('unzip -o -q %s -d %s' % (cgal_file, build_folder))
    os.remove(cgal_file)
  # Now you have the source code.
  helper.PrintWithGreenColor('Downloaded and unzipped CGAL 4.12')
  cgal_dir = ''
  for folder_name in os.listdir(build_folder):
    if 'cgal' in folder_name or 'CGAL' in folder_name:
      cgal_dir = os.path.join(build_folder, folder_name)
      break
  # Add cgal_root to the environment variable list.
  env_variables['CGAL_DIR'] = os.environ['CGAL_DIR'] = cgal_dir

def InstallEigen(root_folder, init=True):
  if init:
    helper.Run('wget https://github.com/eigenteam/eigen-git-mirror/archive/3.3.4.zip')
    cpp_lib_folder = os.path.join(root_folder, 'cpp', 'lib')
    helper.Run('unzip 3.3.4.zip -d %s' % os.path.join(cpp_lib_folder))
    helper.Run('mv %s %s' % (os.path.join(cpp_lib_folder, \
     'eigen-git-mirror-3.3.4'), os.path.join(cpp_lib_folder, 'eigen-3.3.4')))
    helper.Run('rm 3.3.4.zip')
    helper.PrintWithGreenColor('Installed Eigen')

################################################################################
# Variables.
################################################################################
env_variables = {}

################################################################################
# Beginning of the script.
################################################################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--build_dir', default='', help='build directory path.')
    parser.add_argument('-dp', '--deps', action='store_false', help='Disable apt-get & py3 dependencies.')
    parser.add_argument('-eg', '--eigen', action='store_false', help='Disable Eigen install.') 
    parser.add_argument('-cg', '--cgal', action='store_false', help='Disable CGAL install.')
    parser.add_argument('-c', '--cpp', action='store_false', help='Disable source cpp compilation.')
    parser.add_argument('-sk', '--sketch', action='store_false', help='Disable sketch installation.')
    args = parser.parse_args()
    print('Arguments:', args)

    # Usage: python3 install.py -d <build folder>
    if not args.build_dir:
      print('Usage: python3 install.py -d <build_folder>')
      sys.exit(-1)

    build_folder = os.path.realpath(args.build_dir)
    root_folder = HERE
    if not os.path.exists(build_folder):
      os.makedirs(build_folder)
    helper.PrintWithGreenColor('Build folder created :{}'.format(build_folder))
    
    # Add a new environment variable to save the location of the root folder.
    env_variables['CSG_ROOT'] = os.environ['CSG_ROOT'] = root_folder
    
    # Install CGAL.
    InstallCGAL(build_folder, args.eigen)
    
    # Install Eigen-3.3.4.
    InstallEigen(root_folder, args.cgal)
    
    # Compile cpp.
    cpp_build_folder = os.path.join(build_folder, 'cpp')
    if not os.path.exists(cpp_build_folder):
      os.makedirs(cpp_build_folder)
    if args.cpp:
      os.chdir(cpp_build_folder)
      os.environ['CC'] = '/usr/bin/gcc-6'
      os.environ['CXX'] = '/usr/bin/g++-6'
      helper.Run('cmake -DCGAL_DIR=%s %s' % (env_variables['CGAL_DIR'], \
                                             os.path.join(root_folder, 'cpp')))
      helper.Run('make')
      helper.PrintWithGreenColor('C++ program compiled successfully.')
    env_variables['CSG_CPP_EXE'] = os.path.join(cpp_build_folder,
                                                'csg_cpp_command')
    
    # Install Sketch.
    # Try calling Sketch. If it is successful, we are done.
    if CheckSketch(build_folder):
      SaveCustomizedEnvironmentVariables(env_variables, os.path.join(
        build_folder, 'ENVIRONMENT'))
      helper.PrintWithGreenColor('Installation Done.')
      sys.exit(0)
    
    helper.Run('git config --add user.email fake@fake.com')
    helper.Run('git config --add user.name fake')
    # * Download sketch-backend.
    sketch_folder = os.path.join(build_folder, 'sketch')
    if not os.path.exists(sketch_folder):
      os.makedirs(sketch_folder)
    if args.sketch:
      # Sketch-backend.
      os.chdir(sketch_folder)
      helper.Run('git clone https://github.com/asolarlez/sketch-backend.git')

    sketch_backend_folder = os.path.join(sketch_folder, 'sketch-backend')
    env_variables['CSG_SKETCH_BACKEND'] = sketch_backend_folder

    # * build sketch backend
    if args.sketch:
      os.chdir(sketch_backend_folder)
      # # use the commit from around when this project created
      helper.Run('git checkout 6ecbb6f724149d50d290997fef5e2e1e92ab3d9e || true')
      helper.Run('bash autogen.sh')
      helper.Run('./configure')
      helper.Run('make -j2')
      # Interestingly, I need to manually do the following copy and paste work to
      # avoid an error in sketch-frontend.
      sketch_solver_folder = os.path.join(sketch_backend_folder, 'src/SketchSolver')
      shutil.copyfile(os.path.join(sketch_solver_folder, 'libcegis.a'), \
                      os.path.join(sketch_solver_folder, '.libs/libcegis.a'))
      shutil.copyfile(os.path.join(sketch_solver_folder, 'cegis'), \
                      os.path.join(sketch_solver_folder, '.libs/cegis'))
    
    # Download sketch-frontend.
    os.chdir(sketch_folder)
    if args.sketch:
      helper.Run('git clone https://github.com/asolarlez/sketch-frontend.git')
    sketch_frontend_folder = os.path.join(sketch_folder, 'sketch-frontend')
    env_variables['CSG_SKETCH_FRONTEND'] = sketch_frontend_folder
    os.chdir(sketch_frontend_folder)
    # # use the commit from around when this project created
    helper.Run('git checkout 2d7f9fc36bba1d71d65fc07397c82c837f20da96 || true')
    # update frontend-build settings
    shutil.copyfile(os.path.join(root_folder, 'sketch-frontend-pom.xml'), \
                      os.path.join(sketch_frontend_folder, 'pom.xml'))
    if args.sketch:
      helper.Run('make system-install DESTDIR=/usr/bin SUDOINSTALL=1')
    
    # Now check Sketch again.
    if not CheckSketch(build_folder):
      helper.PrintWithRedColor('Failed to install Sketch. Please fix.')
      sys.exit(-1)
    
    SaveCustomizedEnvironmentVariables(env_variables, os.path.join(
      build_folder, 'ENVIRONMENT'))
    helper.PrintWithGreenColor('Installation Done.')


if __name__ == '__main__':
    main()

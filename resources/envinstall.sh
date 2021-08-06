#! /usr/bin/bash
# /usr/bin/env bash
# First check conda version, if no version install miniconda latest.
# Setup directories for project with some user input
# Build environment from user spcified file
# Add alias to .bashrc
echo "Checking for Conda"
conver=$(conda -V)
if [ -z "$conver" ]
then
 echo 'Conda not present. Install Miniconda?(Y/n)'
 read invar
 if [ $invar == Y ]
 then
  echo 'Starting Download'
  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
  bash ./Miniconda3-latest-Linux-x86_64.sh
  cat ./condaconfig >> $HOME/.condarc
  echo "Conda config updated to include:"
  echo "$(cat $HOME/.condarc)"
  echo "Re-run this script from new shell!"
  exit 1
 elif [ $invar != Y ]
 then
  echo 'Skipping install'
  exit 1
 fi
else
# nano tester
 echo "Conda version: "$convar". Continuing environment setup."
 echo 'New Project Name?'
 read pname
 echo 'Path (full) to env file?'
 read envfile
 echo 'Envionment name (4 letters)'
 read envname
fi

maindir="$HOME/PyProj"
projdir="$maindir/$pname"
envpath=$HOME/PyProj/$pname/env/$envname

if [ ! -d "$envpath" ]
then
 mkdir -p "$envpath"
 echo ""$envpath" path created"
else
 echo ""$envpath" path present!"
 echo "Check if path is in use by another environment"
 echo "or try with another project name not in use"
 exit 1
fi

echo 'Building environment...'

bash -c "conda env create --prefix $envpath -f $envfile"
# conda config --set envs_dir $envname

echo 'Adding alias to .bashrc file'
function save-alias() {

    ALIAS_NAME=`echo "$1" | grep -o ".*="`

    # Deleting dublicate aliases
    # sed -i "/alias $ALIAS_NAME/d" $HOME/.bashrc

    # Quoting command: my-alias=command -> my-alias="command"
    QUOTED=`echo "$1"\" | sed "s/$ALIAS_NAME/$ALIAS_NAME\"/g"`

    echo "alias $QUOTED" >> $HOME/.bashrc

    # Loading aliases
    # source $ALIASES_FILE_PATH
}

save-alias $envname="conda activate $envpath"

echo "Alias: $envname added"
. $HOME/.bashrc

echo 'Mission COMPLETE!'

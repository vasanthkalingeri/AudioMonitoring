sudo apt-get install python-bluez;
sudo apt-get install python-alsaaudio;
sudo apt-get install python-mutagen;
wget http://eyed3.nicfit.net/releases/eyeD3-0.7.5.tgz;
tar -xvf eyeD3-0.7.5.tgz;
cd eyeD3-0.7.5/;
sudo python setup.py install;
cd ..;
sudo rm -r eyeD3-0.7.5/;
sudo apt-get install git-core;
#git clone https://github.com/vasanthkalingeri/AudioMonitoring.git;
#cd AudioMonitoring/;
#python main.py

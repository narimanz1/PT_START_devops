Вот такие команды я прописывал:

`sudo apt update -y && sudo apt upgrade -y`

`sudo apt-get install git python3-pip`

`pip3 install ansible`

`sudo apt install sshpass`

`sudo apt install ssh`

Далее изменение прав на машинках для пользователя. Я взял как из лекций - то есть ansible. 

`sudo visudo`

Внутри прописал в конце

`ansible ALL=(ALL:ALL) NOPASSWD:ALL`

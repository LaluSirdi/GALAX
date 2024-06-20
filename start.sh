set -eu

export PYTHONUNBUFFERED=true

VIRTUALENV=.data/venv


if [ ! -d "$HOME/.pyenv" ]; then
  curl https://pyenv.run | bash
fi


export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"


if [ ! -d "$HOME/.pyenv/versions/3.10.0" ]; then
  pyenv install 3.10.0
fi
pyenv global 3.10.0


if [ ! -d $VIRTUALENV ]; then
  python3 -m venv $VIRTUALENV
fi


if [ ! -f $VIRTUALENV/bin/pip ]; then
  curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | $VIRTUALENV/bin/python
fi


$VIRTUALENV/bin/pip install -r requirements.txt


$VIRTUALENV/bin/python3 app.py
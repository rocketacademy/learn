# Learn

This is Rocket's learning management system, meant to streamline operations for administrators and improve teaching and learning experiences for section leaders and students.

It is built with Django, hosted on Heroku, and connected to a PostgreSQL database.

### Install `pyenv`, `python`, `pipenv`, and `virtualenvwrapper`
Since Learn is built with Django, we will need to set up our Python environment locally. Doing this wrongly could result in confusion about which Python is running. The following steps are summarised from the following articles:
- [Setting Python3 as default on Mac](https://opensource.com/article/19/5/python-3-default-mac)
- [Using Pyenv to run multiple versions of Python](https://opensource.com/article/20/4/pyenv)
- [Setting up virtual environment for Python on Mac](https://opensource.com/article/19/6/python-virtual-environments-mac)

1. Install `pyenv` to help manage our Python environments.<br>
   `$ brew install pyenv`
2. Install the Python version we need.<br>
   `$ pyenv install 3.9.10`
3. Set this newly installed version as the global default.<br>
   `$ pyenv global 3.9.10`.
4. Check that the default has been set successfully.<br>
   `$ pyenv version`<br>
   `$ 3.9.10 (set by /Users/<yourusername>/.pyenv/version`
5. Install `pipenv` to help manage packages.<br>
   `$ brew install pipenv`
6. Add the following to your `~/.zshrc` file.
   - Configure shell's environment for pyenv:<br>
     `if command -v pyenv 1>/dev/null 2>&1; then
        eval "$(pyenv init -)"
     fi`
   - Tell shell to use pyenv's version of Python whenever we run a command<br>
     `PATH=$(pyenv root)/shims:$PATH`
7. Check that we have dependencies required for `pyenv`.<br>
   `$ brew install zlib sqlite`
8. Install `virtualenvwrapper` into the current Python environment<br>
   `$ $(pyenv which python3) -m pip install virtualenvwrapper`
9. Add the following to your `~/.zshrc` file.<br>
   - Specify that we want to regularly go to our virtual environment directory<br>
     `export WORKON_HOME=~/.virtualenvs`
   - Make a virtual environment directory in a virtual environment if one doesn't already exist<br>
     `mkdir -p $WORKON_HOME`
   - Activate the new virtual environment by calling this script<br>
     `. ~/.pyenv/versions/3.9.10/bin/virtualenvwrapper.sh`
10. Restart your terminal and check that you see the following output. This means that `virtualenvwrapper` is initialising the environment. We will create a virtual environment after we clone Learn's code repository.
    ```
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/premkproject
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/postmkproject
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/initialize
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/premkvirtualenv
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/postmkvirtualenv
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/prermvirtualenv
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/postrmvirtualenv
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/predeactivate
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/postdeactivate
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/preactivate
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/postactivate
    virtualenvwrapper.user_scripts creating /Users/samanthakoh/.virtualenvs/get_env_details
    ```


### Set up Learn in your local environment
1. Navigate to the repository you want Learn to reside in.
2. Clone this [codebase](https://github.com/rocketacademy/learn)<br>
   `$ git clone https://github.com/rocketacademy/learn.git`
3. Retrieve environment variables from 1Password and place them in a .env file in Learn's root directory.
4. In Learn folder, create a virtual environment<br>
   `$ mkvirtualenv $(basename $(pwd))`<br>
5. You should see the following when the virtual environment has been created and activated.<br>
   `(learn) $`
6. From now on, navigate to the project directory to activate or deactivate the virtual environment.<br>
   `$ pipenv shell` or `$ workon learn`
   `$ deactivate`

### Install certifi since Python no longer relies on macOS' openSSL certificates
1. Create `install_certifi.py` file
2. Copy and paste code from this [gist](https://gist.github.com/marschhuynh/31c9375fc34a3e20c2d3b9eb8131d8f3)
3. Run `python install_ceritif.py`

### Install and set up Postgres database
1. Install `Postgres`<br>
   `$ brew install postgres`
2. Start database<br>
   `$ pg_ctl -D /opt/homebrew/var/postgres start`
3. Check that `Postgres` has been installed
   `$ psql postgres`<br>
   `$ \du`
4. Create Learn database<br>
   `$ createdb learn`
5. Check that database was created<br>
   `$ psql learn`


### Verify that set-up is complete
`$ python manage.py show_urls`<br>
`$ python manage.py migrate`<br>
`$ python manage.py runserver`


### Stripe webhook
In a separate terminal window, listen to Stripe webhook in order to receive payments and complete transactions<br>
`$ stripe listen --forward-to localhost:8000/payment/stripe/webhook/`

#!/usr/bin/env puma

# Start Puma with next command:
# RAILS_ENV=production bundle exec puma -C ./config/puma.rb

# uncomment and customize to run in non-root path
# note that config/gitlab.yml web path should also be changed
# ENV['RAILS_RELATIVE_URL_ROOT'] = "/gitlab"

application_path = '/srv/gitlab/gitlab'

# The directory to operate out of.
#
# The default is the current directory.
#
directory application_path

# Set the environment in which the rack's app will run.
#
# The default is âdevelopmentâ
                              #
environment 'production'

# Daemonize the server into the background. Highly suggest that
# this be combined with âpidfileâstdout_redirectâ
                                                 #
# The default is âfalseâ
                        #
daemonize true

# Store the pid of the server in the file at âpathâ
                                                   #
pidfile "#{application_path}/tmp/pids/puma.pid"

# Use âpathâ
            # used by âpumactlâ
                               #
state_path "#{application_path}/tmp/pids/puma.state"

# Redirect STDOUT and STDERR to files specified. The 3rd parameter
# (âappendâ
           # âfalseâ
                    #
stdout_redirect "#{application_path}/log/puma.stdout.log", "#{application_path}/log/puma.stderr.log"

# stdout_redirect '/u/apps/lolcat/log/stdout', '/u/apps/lolcat/log/stderr', true

# Disable request logging.
#
# The default is âfalseâ
                        #
# quiet

# Configure âminâ
# requests and âmaxâ
#
# The default is â0, 16â
#
# threads 0, 16

# Bind the server to âurlâtcp://âunix://âssl://â
# accepted protocols.
#
# The default is âtcp://0.0.0.0:9292â
#
# bind 'tcp://0.0.0.0:9292'
bind "unix://#{application_path}/tmp/sockets/gitlab.socket"

# Instead of âbind 'ssl://127.0.0.1:9292?key=path_to_key&cert=path_to_cert'â
# can also use the âssl_bindâ
#
# ssl_bind '127.0.0.1', '9292', { key: path_to_key, cert: path_to_cert }

# Code to run before doing a restart. This code should
# close log files, database connections, etc.
#
# This can be called multiple times to add code each time.
#
# on_restart do
#   puts 'On restart...'
# end

# Command to use to restart puma. This should be just how to
# load puma itself (ie. 'ruby -Ilib bin/puma'), not the arguments
# to puma, as those are the same as the original process.
#
# restart_command '/u/app/lolcat/bin/restart_puma'

# === Cluster mode ===

# How many worker processes to run.
#
# The default is â0â
#
# workers 2

# Code to run when a worker boots to setup the process before booting
# the app.
#
# This can be called multiple times to add hooks.
#
# on_worker_boot do
#   puts 'On worker boot...'
# end

# === Puma control rack application ===

# Start the puma control rack application on âurlâ
# be communicated with to control the main server. Additionally, you can
# provide an authentication token, so all requests to the control server
# will need to include that token as a query parameter. This allows for
# simple authentication.
#
# Check out https://github.com/puma/puma/blob/master/lib/puma/app/status.rb
# to see what the app has available.
#
# activate_control_app 'unix:///var/run/pumactl.sock'
# activate_control_app 'unix:///var/run/pumactl.sock', { auth_token: '12345' }
# activate_control_app 'unix:///var/run/pumactl.sock', { no_token: true }

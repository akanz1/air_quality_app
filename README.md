# Air Quality App

This app reads in data from a sensor, preprocesses it and stores it in an InfluxDB for visualization with Grafana. Monitors CO2, Temperature, Humidity, Particulate Matter/Dust Particles (2.5PM and 10PM) and more.

<p align="center"><img src="https://raw.githubusercontent.com/akanz1/air_quality_app/main/screenshots/dashboard.png" alt="dashboard" width="1312" height="498"></p>


### Useful commands

`sudo su -`

Check disk usage: `du -hxs /var/lib/docker/ | sort -rh | head -n 40`

Free disk space: `docker system prune -a`


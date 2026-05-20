FROM jenkins/jenkins:lts

# Skip initial setup wizard
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Install plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

USER jenkins

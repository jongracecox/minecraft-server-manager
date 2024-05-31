from decouple import config


JAVA_HOME = config("JAVA_HOME", default="/usr/local/Cellar/openjdk/20.0.1/libexec/openjdk.jdk/Contents/Home")
JAVA_BIN = f"{JAVA_HOME}/bin/java"
FROM gradle:6.6.1-jdk14 AS build
COPY --chown=gradle:gradle . /home/gradle
WORKDIR /home/gradle
RUN gradle build --no-daemon

FROM openjdk:14-jdk-alpine
RUN mkdir /app

EXPOSE 8079

COPY --from=build /home/gradle/build/libs/jsqlparser-as-a-service.jar /app/app.jar
ENTRYPOINT ["java","-jar","/app/app.jar"]
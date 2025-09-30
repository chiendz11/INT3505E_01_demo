package com.soap;

import jakarta.jws.WebService;
import jakarta.xml.ws.Endpoint;

@WebService(endpointInterface = "com.soap.HelloService")
public class HelloServiceImpl implements HelloService {
    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }

    public static void main(String[] args) {
        Endpoint.publish("http://localhost:8080/hello", new HelloServiceImpl());
        System.out.println("Service is running at http://localhost:8080/hello?wsdl");
    }
}

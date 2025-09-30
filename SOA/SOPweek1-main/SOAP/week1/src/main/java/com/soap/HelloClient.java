package com.soap;

import jakarta.xml.ws.Service;
import javax.xml.namespace.QName;
import java.net.URL;

public class HelloClient {
    public static void main(String[] args) throws Exception {
        URL wsdlUrl = new URL("http://localhost:8080/hello?wsdl");
        QName qname = new QName("http://soap.com/", "HelloServiceImplService");

        Service service = Service.create(wsdlUrl, qname);
        HelloService hello = service.getPort(HelloService.class);
        System.out.println(hello.sayHello("World"));
    }
}

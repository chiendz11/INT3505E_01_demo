package com.soap;

import jakarta.jws.WebService;
import jakarta.jws.WebMethod;

@WebService
public interface HelloService {
    @WebMethod
    String sayHello(String name);
}

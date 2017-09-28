package org.robocode.config;


import org.robocode.communication.tmp.RSecureChatServer;
import org.robocode.communication.tmp.RSecureChatServerHandler;
import org.robocode.communication.tmp.UDPVideoServer;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.FilterType;
import org.springframework.stereotype.Controller;

@Configuration
@ComponentScan(basePackages = "org.robocode", excludeFilters = {
        @ComponentScan.Filter(value = Controller.class, type = FilterType.ANNOTATION),
        @ComponentScan.Filter(value = Configuration.class, type = FilterType.ANNOTATION)
})
public class AppConfig {

    @Bean
    public RSecureChatServerHandler secureChatServerHandler(){
        return new RSecureChatServerHandler();
    }

    @Bean
    public RSecureChatServer chatServer(RSecureChatServerHandler secureChatServerHandler){
        try {
            return new RSecureChatServer(secureChatServerHandler);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }


    @Bean
    public UDPVideoServer video(){
        return  new UDPVideoServer();
    }
}

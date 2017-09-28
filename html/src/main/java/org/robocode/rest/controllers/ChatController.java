package org.robocode.rest.controllers;

import org.robocode.communication.tmp.RSecureChatServerHandler;
import org.robocode.core.Message;
import org.robocode.core.OutputMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.handler.annotation.SendTo;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;

@RestController
@RequestMapping("/")
public class ChatController {

    @Autowired
    public ChatController(RSecureChatServerHandler secureChatServerHandler) {
        this.secureChatServerHandler = secureChatServerHandler;
    }

    @MessageMapping("/chat")
    @SendTo("/topic/message")
    public OutputMessage sendMessage(Message message) {
        this.secureChatServerHandler.sendMessage(message.getMessage());

        if(message.getMessage().contains(";") || message.getId() == 1 || message.getId() == 2) {
            return new OutputMessage(message, new Date());
        }
        else {
            message.setMessage("");
            message.setTip(" ");
            return new OutputMessage(message, new Date());
        }

    }

    private RSecureChatServerHandler secureChatServerHandler;
}

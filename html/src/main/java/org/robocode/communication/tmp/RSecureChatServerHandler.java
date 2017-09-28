package org.robocode.communication.tmp;

import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.SimpleChannelInboundHandler;
import io.netty.channel.group.ChannelGroup;
import io.netty.channel.group.DefaultChannelGroup;
import io.netty.util.concurrent.GlobalEventExecutor;
import org.robocode.core.Message;
import org.robocode.core.OutputMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import java.text.SimpleDateFormat;
import java.util.Date;

@ChannelHandler.Sharable
public class RSecureChatServerHandler extends SimpleChannelInboundHandler<String> {
    private static final ChannelGroup channels;

    public RSecureChatServerHandler() {
    }

    public void channelActive(ChannelHandlerContext ctx) {
        channels.add(ctx.channel());
    }

    public void channelRead0(ChannelHandlerContext ctx, String msg) throws Exception {

        Message message = new Message();
        message.setId(1);
        message.setMessage(msg);
        message.setTip("senzor");
        OutputMessage outputMessage = new OutputMessage(message, new Date());
        messageSender.convertAndSend("/topic/message", outputMessage);
    }

    public void sendMessage(String message) {
        Thread t = new Thread(() -> {
            new SimpleDateFormat("HH:mm:ss");
            new Date();
            channels.forEach((channel) -> channel.writeAndFlush(String.format("%s\r\n", message)));
        });
        t.start();
    }

    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
    }

    public void channelUnregistered(ChannelHandlerContext ctx) throws Exception {
        super.channelUnregistered(ctx);
        channels.remove(ctx.channel());
        ctx.close();
    }

    static {
        channels = new DefaultChannelGroup(GlobalEventExecutor.INSTANCE);
    }

    @Autowired
    private SimpMessagingTemplate messageSender;
}

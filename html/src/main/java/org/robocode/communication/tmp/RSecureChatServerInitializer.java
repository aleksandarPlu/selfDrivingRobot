package org.robocode.communication.tmp;

import io.netty.channel.ChannelHandler;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.ChannelPipeline;
import io.netty.channel.socket.SocketChannel;
import io.netty.handler.codec.DelimiterBasedFrameDecoder;
import io.netty.handler.codec.Delimiters;
import io.netty.handler.codec.string.StringDecoder;
import io.netty.handler.codec.string.StringEncoder;
import org.springframework.beans.factory.annotation.Autowired;

public class RSecureChatServerInitializer extends ChannelInitializer<SocketChannel> {

    @Autowired
    public RSecureChatServerInitializer(RSecureChatServerHandler secureChatServerHandler) {
        this.secureChatServerHandler = secureChatServerHandler;
    }

    public void initChannel(SocketChannel ch) throws Exception {
        ChannelPipeline pipeline = ch.pipeline();
        pipeline.addLast(new ChannelHandler[]{new DelimiterBasedFrameDecoder(8192, Delimiters.lineDelimiter())});
        pipeline.addLast(new ChannelHandler[]{new StringDecoder()});
        pipeline.addLast(new ChannelHandler[]{new StringEncoder()});
        pipeline.addLast(new ChannelHandler[]{this.secureChatServerHandler});
    }

    //property
    private RSecureChatServerHandler secureChatServerHandler;
}


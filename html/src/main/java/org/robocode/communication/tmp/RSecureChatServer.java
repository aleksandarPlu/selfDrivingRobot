package org.robocode.communication.tmp;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.handler.logging.LogLevel;
import io.netty.handler.logging.LoggingHandler;

public class RSecureChatServer {
    private static final int PORT = Integer.parseInt(System.getProperty("port", "8992"));

    public RSecureChatServer(RSecureChatServerHandler secureChatServerHandler)  {
        new Thread(()->{
            EventLoopGroup bossGroup = new NioEventLoopGroup(1);
            NioEventLoopGroup workerGroup = new NioEventLoopGroup();

            try {
                ServerBootstrap b = new ServerBootstrap();
                ((ServerBootstrap) ((ServerBootstrap) b.group(bossGroup, workerGroup).channel(NioServerSocketChannel.class)).handler(new LoggingHandler(LogLevel.INFO))).childHandler(new RSecureChatServerInitializer(secureChatServerHandler));
                b.bind(PORT).sync().channel().closeFuture().sync();
            }catch (Exception e){
                e.printStackTrace();
            } finally {
                bossGroup.shutdownGracefully();
                workerGroup.shutdownGracefully();
            }

        }).start();

    }
}

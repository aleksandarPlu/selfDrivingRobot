package org.robocode.communication.tmp;

import org.robocode.core.Message;
import org.robocode.core.OutputMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.messaging.simp.SimpMessagingTemplate;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.util.Date;

public class UDPVideoServer {

    @Autowired
    private SimpMessagingTemplate messageSender;

    private long count = 0;
    
    public UDPVideoServer() {
        new Thread(()->{
            byte[] msg;
            while (true) {
                msg = receiveVide();
                if (msg != null) {
                    Message message = new Message();
                    message.setId(2);
                    message.setMessage(new String(msg));
                    message.setTip("video");
                    OutputMessage outputMessage = new OutputMessage(message, new Date());
                    messageSender.convertAndSend("/topic/message", outputMessage);
                }
            }
        }).start();
    }

    public static byte[] receiveVide(){
        try
        {
            DatagramSocket sock = new DatagramSocket(8993) ;
            byte soundpacket[] = new byte[128000] ;
            DatagramPacket datagram = new DatagramPacket( soundpacket , soundpacket.length ) ;
            sock.receive( datagram ) ;
            sock.close() ;
            return datagram.getData();
        }
        catch( Exception e )
        {
            System.out.println(" Unable to send soundpacket using UDP " ) ;
            return null ;
        }
    }
}

package org.robocode.core;

public class Message {

    //constructor
    public Message() {
    }

    public Message(String message, String tip, int id) {
        this.message = message;
        this.tip = tip;
        this.id = id;
    }

    //getters and setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getTip() {
        return tip;
    }

    public void setTip(String type) {
        this.tip = type;
    }

    @Override
    public String toString() {
        return "Message{" +
                "message='" + message + '\'' +
                "tip='" + tip + '\'' +
                ", id=" + id +
                '}';
    }

    //properties
    private String message;
    private String tip;
    private int id;
}

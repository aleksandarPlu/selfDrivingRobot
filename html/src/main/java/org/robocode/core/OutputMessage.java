package org.robocode.core;

import java.util.Date;

public class OutputMessage extends Message {

    private Date time;

    public OutputMessage(Message original, Date time) {
        super(original.getMessage(), original.getTip(), original.getId());
        if (original.getTip().equals("video"))
            this.time = new Date(0);
        else
            this.time = time;

    }

    public Date getTime() {
        return time;
    }

    public void setTime(Date time) {
        this.time = time;
    }
}
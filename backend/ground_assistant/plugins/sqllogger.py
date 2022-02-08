class MySQLLogger:
    def __init__(self, path):
        from ground_assistant.common.load import ReadConfig, mySQL
        from ground_assistant.common.logger import Logger
        configs = ReadConfig(path)
        self.logging = Logger(config_obj = configs, path = path, name = "forktodb.log")
        self.keyerrorlogging = Logger(config_obj = configs, path = path, name = "keyerror.log")
        self.mysql = mySQL(configs)
        self.stats = 0
        self.logging.append("Fork ready...")

        from datetime import date
        self.date = date
        x = {"CREATE TABLE IF NOT EXISTS " +
             str(date.today()).replace("-","_") +                          #The name is todays date,
             " ( time TIME," +                                             #First row is a timestamp,
             " ref_time TIME," +                                           #second row is another timestamp,
             " beacon_type VARCHAR(255)," +                                #the type of beacon
             " receiver VARCHAR(255)," +                                   #the receiver,
             " device_id VARCHAR(6)," +                                    #FLARM ID,
             " type VARCHAR(20)," +                                        #type of aircraft,
             " north DOUBLE(180,7)," +                                     #coordinates north,
             " east DOUBLE(180,7)," +                                      #coordinates south,
             " groundspeed INT(255)," +                                    #groundspeed,
             " msl INT(255)," +                                            #hight above sealevel (MSL),
             " climbrate FLOAT(10)," +                                     #and the climbrate
             " turnrate FLOAT(10)," +                                      #and the turnrate
             " gps_horizontal FLOAT(10)," +                                #and the climbrate
             " gps_vertical FLOAT(10));"}                                  #and the climbrate

        self.mysql.sendquery(''.join(list(x)))
        self.logging.append("Created table")

    def write(self, beacon):
        try:
            x = {"INSERT INTO " +
                 str(self.date.today()).replace("-","_") +
                 " VALUES (" +
                 "\"" + str(beacon["timestamp"].time()) + "\"," +
                 "\"" + str(beacon["reference_timestamp"].time()) + "\"," +
                 "\"" + beacon["beacon_type"] + "\"," +
                 "\"" + beacon["receiver_name"] + "\"," +
                 "\"" + beacon["address"] + "\"," +
                 "\"" + str(beacon["aircraft_type"]) + "\"," +
                 str(round(beacon["latitude"],7)) + "," +
                 str(round(beacon["longitude"],7)) + "," +
                 str(round(beacon["ground_speed"],2)) + "," +
                 str(round(beacon["altitude"],2)) + "," +
                 str(round(beacon["climb_rate"],2)) + "," +
                 str(round(beacon["turn_rate"],2)) + "," +
                 str(beacon["gps_quality"]["horizontal"]) + "," +
                 str(beacon["gps_quality"]["vertical"]) + ");"}
        except KeyError as e:
            self.keyerrorlogging.append(e)
            return False

        self.mysql.sendquery(''.join(list(x)))
        self.mysql.commit()
        self.stats += 1
        return True

    def close(self):
        self.mysql.commit()
        self.mysql.close()
        self.logging.append("Wrote " + str(self.stats) + " beacons to MySQL.")
        self.logging.append("Fork closed.")
        self.logging.close()
        return True
drop table if exists subscribers;
drop table if exists devices;
create table subscribers (
  id INTEGER PRIMARY KEY,
  ip text unique not null
);
create table devices (
  id INTEGER PRIMARY KEY,
  mac text unique,
  uuid text,
  majorid int,
  minorid int,
  rssi int,
  tx_calibrated int
);

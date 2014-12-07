drop table if exists subscribers;
drop table if exists devices;
create table subscribers (
  id INTEGER PRIMARY KEY,
  ip text unique not null
);
create table devices (
  mac text unique,
  uuid text PRIMARY KEY,
  majorid int,
  minorid int,
  rssi int,
  tx_calibrated int
);

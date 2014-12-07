drop table if exists subscribers;
drop table if exists devices;
create table subscribers (
  id integer primary key autoincrement,
  ip text not null
);
create table devices (
  id integer primary key autoincrement,
  mac text unique,
  uuid text,
  majorid int,
  minorid int,
  rssi int,
  tx_calibrated int
);

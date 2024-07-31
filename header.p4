#ifndef __HEADER_H__
#define __HEADER_H__ 1

#include <core.p4>
#include <v1model.p4>

struct ingress_metadata_t {
    bit<32> nhop_ipv4;
}

@metadata
struct intrinsic_metadata_t {
    bit<48> ingress_global_timestamp;
    bit<32> lf_field_list;
    bit<16> mcast_grp;
    bit<16> egress_rid;
    bit<8>  resubmit_flag;
    bit<8>  recirculate_flag;
}

@metadata @name("queueing_metadata")
struct queueing_metadata_t {
    bit<48> enq_timestamp;
    bit<16> enq_qdepth;
    bit<32> deq_timedelta;
    bit<16> deq_qdepth;
}

@metadata @name("int_metadata")
struct int_metadata_t {
    bit<8> device_no;
}

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header arp_t {
    bit<16> arpHdr;     /* format of hardware address */
    bit<16> arpPro;     /* format of protocol address */
    bit<8>  arpHln;     /* length of hardware address */
    bit<8>  arpPln;     /* length of protocol address */
    bit<16> arpOp;      /* ARP/RARP operation */
    bit<48> arpSha;     /* sender hardware address */
    bit<32> arpSpa;     /* sender protocol address */
    bit<48> arpTha;     /* target hardware address */
    bit<32> arpTpa;     /* target protocol address */
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;       // udp 17, tcp 6
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> len;
    bit<16> hdrChecksum;
}


header sr_t {
    bit<512> routingList;
}

header device_no_t {
    bit<8>  device_no;
}

header ingress_port_t {
    bit<16>  ingress_port;
}

header egress_port_t {
    bit<16>  egress_port;
}

header ingress_global_timestamp_t {
    bit<48>  ingress_global_timestamp;
}

header egress_global_timestamp_t {
    bit<48>  egress_global_timestamp;
}

header enq_qdepth_t {
    bit<24>  enq_qdepth;
}

header deq_qdepth_t {
    bit<24>  deq_qdepth;
}

header ingress_byte_count_t {
    bit<32>  ingress_byte_count;
}

header egress_byte_count_t {
    bit<32>  egress_byte_count;
}

struct metadata {
    @name("ingress_metadata")
    ingress_metadata_t   ingress_metadata;
    @name("intrinsic_metadata")
    intrinsic_metadata_t intrinsic_metadata;
    @name("queueing_metadata")
    queueing_metadata_t queueing_metadata;
    @name("int_metadata")
    int_metadata_t int_metadata;
}

struct headers {
    @name("ethernet")
    ethernet_t  ethernet;
    @name("arp")
    arp_t       arp;
    @name("ipv4")
    ipv4_t      ipv4;
    @name("udp")
    udp_t       udp;
    @name("sr")
    sr_t        sr;
    @name("device_no")
    device_no_t    device_no;

    ingress_port_t        ingress_port;

    egress_port_t        egress_port;

    ingress_global_timestamp_t        ingress_global_timestamp;

    egress_global_timestamp_t        egress_global_timestamp;

    enq_qdepth_t        enq_qdepth;

    deq_qdepth_t        deq_qdepth;

    ingress_byte_count_t        ingress_byte_count;

    egress_byte_count_t        egress_byte_count;
}

#endif // __HEADER_H__

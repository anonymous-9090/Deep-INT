#include <core.p4>
#include <v1model.p4>

#include "header.p4"
#include "parser.p4"

#define COUNTER_SIZE 32w16
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
register<bit<32>>(1) total_bytes1;
register<bit<32>>(1) total_bytes2;

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    counter(COUNTER_SIZE, CounterType.packets) egress_counter;

    @name("_drop")
    action _drop() {
        mark_to_drop(standard_metadata);
    }
    @name("count_bytes")
    action count_bytes() {
        bit<32> byte_count;
        total_bytes2.read(byte_count, 0);
        byte_count = byte_count + (bit<32>)standard_metadata.packet_length;
        total_bytes2.write(0, byte_count);
    }
    @name("do_int")
    action do_int() {
    }

    @name("udp_int")
    table udp_int {
        actions = {
            do_int;
        }
        key = {}
        default_action = do_int();
    }

    apply {
        udp_int.apply();
        egress_counter.count((bit<32>)standard_metadata.egress_port);
        bit<8> bitmap = (bit<8>) hdr.sr.routingList;
        hdr.sr.routingList=hdr.sr.routingList>>14;
        count_bytes();
        bit<32> reg_value1;
        bit<32> reg_value2;
        total_bytes1.read(reg_value1, 0);
        total_bytes2.read(reg_value2, 0);
        hdr.udp.len = hdr.udp.len + 16w1;
        hdr.udp.hdrChecksum = 16w0;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w1;
        hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w1;
        hdr.device_no.setValid();
        hdr.device_no.device_no = meta.int_metadata.device_no;
        if (hdr.sr.isValid()) {
          if ((bitmap & 8w1) != 0) {
              hdr.udp.len = hdr.udp.len + 16w2;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w2;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w2;
              hdr.ingress_port.setValid();
              hdr.ingress_port.ingress_port = (bit<16>)standard_metadata.ingress_port;
          }

          if ((bitmap & 8w2) != 0) {
              hdr.udp.len = hdr.udp.len + 16w2;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w2;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w2;
              hdr.egress_port.setValid();
              hdr.egress_port.egress_port = (bit<16>)standard_metadata.egress_port;
          }

          if ((bitmap & 8w4) != 0) {
              hdr.udp.len = hdr.udp.len + 16w6;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w6;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w6;
              hdr.ingress_global_timestamp.setValid();
              hdr.ingress_global_timestamp.ingress_global_timestamp = (bit<48>)standard_metadata.ingress_global_timestamp;
          }

          if ((bitmap & 8w8) != 0) {
              hdr.udp.len = hdr.udp.len + 16w6;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w6;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w6;
              hdr.egress_global_timestamp.setValid();
              hdr.egress_global_timestamp.egress_global_timestamp = (bit<48>)standard_metadata.egress_global_timestamp;
          }

          if ((bitmap & 8w16) != 0) {
              hdr.udp.len = hdr.udp.len + 16w3;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w3;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w3;
              hdr.enq_qdepth.setValid();
              hdr.enq_qdepth.enq_qdepth = (bit<24>)standard_metadata.enq_qdepth;
          }

          if ((bitmap & 8w32) != 0) {
              hdr.udp.len = hdr.udp.len + 16w3;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w3;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w3;
              hdr.deq_qdepth.setValid();
              hdr.deq_qdepth.deq_qdepth = (bit<24>)standard_metadata.deq_qdepth;
          }

          if ((bitmap & 8w64) != 0) {
              hdr.udp.len = hdr.udp.len + 16w4;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w4;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w4;
              hdr.ingress_byte_count.setValid();
              hdr.ingress_byte_count.ingress_byte_count = (bit<32>) reg_value1;
          }

          if ((bitmap & 8w128) != 0) {
              hdr.udp.len = hdr.udp.len + 16w4;
              hdr.ipv4.totalLen = hdr.ipv4.totalLen + 16w4;
              hdr.ipv4.hdrChecksum = hdr.ipv4.hdrChecksum - 16w4;
              hdr.egress_byte_count.setValid();
              hdr.egress_byte_count.egress_byte_count = (bit<32>) reg_value2;
          }
        }
    }
}

control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {

    counter(COUNTER_SIZE,CounterType.packets) ingress_counter;
    register<bit<512>>(1024) sr_routing_list_reg;
    register<bit<9>>(1024) sr_routing_list_reg1;
    register<bit<9>>(1024) sr_routing_list_reg2;

    @name("forward")
    action forward(macAddr_t dstAddr) {
        hdr.ethernet.dstAddr = dstAddr;
    }
    @name("count_bytes")
    action count_bytes() {
        bit<32> byte_count;
        total_bytes1.read(byte_count, 0);
        byte_count = byte_count + (bit<32>)standard_metadata.packet_length;
        total_bytes1.write(0, byte_count);
    }
    @name("_drop")
    action _drop() {
        mark_to_drop(standard_metadata);
    }
    @name("l2setmetadata")
    action l2setmetadata(bit<9> port) {
        standard_metadata.egress_spec = port;
        standard_metadata.egress_port = port;
    }
    @name("l2setmetadataecmp")
    action l2setmetadataecmp(bit<2> routeNum, bit<16> portData) {
        bit<32> result=32w0;
        random(result,32w0,(bit<32>)(routeNum-2w1));
        bit<16> data=portData;
        if (result == 32w1) {
            data=portData>>4;
        }else if(result == 32w2){
            data=portData>>8;
        }else if(result==32w3){
            data=portData>>4;
            data=portData>>8;
        }
        bit<9> port=(bit<9>)((bit<4>)data);
        standard_metadata.egress_spec = port;
        standard_metadata.egress_port = port;
    }
    @name("arpreply")
    action arpreply(bit<48>repmac) {
        standard_metadata.egress_spec = standard_metadata.ingress_port;
        standard_metadata.egress_port = standard_metadata.ingress_port;
        hdr.ethernet.srcAddr=repmac;
        hdr.ethernet.dstAddr=hdr.arp.arpSha;
        bit<32> tempip;
        tempip=hdr.arp.arpSpa;
        hdr.arp.arpSpa=hdr.arp.arpTpa;
        hdr.arp.arpTpa=tempip;
        hdr.arp.arpTha=hdr.arp.arpSha;
        hdr.arp.arpSha=repmac;
    }
    @name("srrouting")
    action srrouting() {
        // read 4 bit from routingList use listPosition
        // and set it to egress metadata
        sr_routing_list_reg.write(0, hdr.sr.routingList);
        bit<14> routing_bits = (bit<14>)hdr.sr.routingList;
        bit<6> port = (bit<6>)(routing_bits >> 8);
        standard_metadata.egress_spec = (bit<9>)port+9w1;
        standard_metadata.egress_port = (bit<9>)port+9w1;
        sr_routing_list_reg1.write(0, standard_metadata.egress_spec);
        sr_routing_list_reg2.write(0, standard_metadata.egress_port);
    }
    @name("setdeviceno")
    action setdeviceno(bit<8> device_no) {
        meta.int_metadata.device_no=device_no;
    }
    @name("ipv4_forward")
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
            hdr.ipv4.dstAddr = (bit<32>) 0x0A00023C;
            standard_metadata.egress_spec = port;
            hdr.ethernet.dstAddr = dstAddr;
            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    @name("dotrans")
    table dotrans {
        actions = {
            l2setmetadataecmp;
            NoAction;
        }
        key = {
            hdr.ethernet.srcAddr:exact;
            hdr.ethernet.dstAddr:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("ipv4_lpm")
    table ipv4_lpm {
        key = {
        }
        actions = {
            forward;
            NoAction;
        }
        size = 1024;
        default_action = forward(0x112233445566);
    }
    @name("ipv4")
    table ipv4 {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            NoAction;
            _drop;
        }
        size = 1024;
        default_action = NoAction();
    }
    @name("dosocket")
    table dosocket {
        actions = {
            l2setmetadata;
            NoAction;
        }
        key = {
            hdr.udp.dstPort:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("doarp")
    table doarp {
        actions = {
            arpreply;
            NoAction;
        }
        key = {
            hdr.arp.arpTha:exact;
            hdr.arp.arpTpa:exact;
        }
        size=512;
        default_action=NoAction();
    }
    @name("dosr")
    table dosr {
        actions = {
            srrouting;
        }
        key={}
        default_action=srrouting();
    }
    @name("setmetadata")
    table setmetadata {
        actions = {
            setdeviceno;
            NoAction;
        }
        key={}
        default_action=NoAction();
    }
    apply {
        count_bytes();
        setmetadata.apply();

        if (hdr.ipv4.isValid()) {
            if(hdr.sr.isValid()) {
                dosr.apply();
                ipv4.apply();
                if(standard_metadata.egress_spec == 1){
                    ipv4_lpm.apply();
                }
            }
        }
         else if(hdr.arp.isValid()) {
            doarp.apply();
            dosocket.apply();
        }
        ingress_counter.count((bit<32>)standard_metadata.ingress_port);
    }
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;

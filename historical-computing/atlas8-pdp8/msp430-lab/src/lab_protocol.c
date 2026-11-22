#include "lab_protocol.h"
#include <string.h>
uint16_t lab_crc(const uint8_t *data, uint8_t len) {
    uint16_t crc=0xFFFF;
    uint8_t i,j;
    for (i=0;i<len;i++) {
        crc ^= ((uint16_t)data[i]) << 8;
        for(j=0;j<8;j++) crc = (uint16_t)((crc<<1) ^ ((crc&0x8000) ? 0x1021 : 0));
    }
    return crc;
}
uint8_t lab_pack(uint8_t seq, uint8_t op, const uint8_t *data, uint8_t len, uint8_t *out) {
    uint16_t crc;
    uint8_t i;
    if (len>LAB_MAX_PAYLOAD) return 0;
    out[0]=LAB_SYNC;out[1]=LAB_VERSION;out[2]=seq;out[3]=op;out[4]=len;
    for(i=0;i<len;i++)out[5+i]=data[i];
    crc=lab_crc(out+1,(uint8_t)(4+len));
    out[5+len]=(uint8_t)(crc>>8);out[6+len]=(uint8_t)crc;
    return (uint8_t)(7+len);
}
uint8_t lab_feed(struct lab_parser *p, uint8_t byte, struct lab_request *r) {
    uint8_t expected;
    uint16_t received;
    if (p->used==0 && byte!=LAB_SYNC) return 0;
    if (p->used >= LAB_FRAME_MAX) {p->used=0;p->errors++;return 0;}
    p->bytes[p->used++]=byte;
    if (p->used>=5 && (p->bytes[1]!=LAB_VERSION || p->bytes[4]>LAB_MAX_PAYLOAD)) {
        p->used=0;p->errors++;return 0;
    }
    if (p->used<5) return 0;
    expected=(uint8_t)(7+p->bytes[4]);
    if (p->used<expected) return 0;
    received=(uint16_t)((((uint16_t)p->bytes[expected-2])<<8)|p->bytes[expected-1]);
    if (received != lab_crc(p->bytes+1,(uint8_t)(expected-3))) {
        p->used=0;p->errors++;return 0;
    }
    r->seq=p->bytes[2];r->op=p->bytes[3];r->len=p->bytes[4];
    memcpy(r->data,p->bytes+5,r->len);
    p->used=0;
    return 1;
}

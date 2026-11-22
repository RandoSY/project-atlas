#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../src/lab_protocol.h"
int main(void) {
    struct lab_parser parser = {{0},0,0};
    struct lab_request request;
    uint8_t frame[LAB_FRAME_MAX],bad[LAB_FRAME_MAX];
    const uint8_t vector[]="123456789";
    uint8_t length,i,got=0;
    assert(lab_crc(vector,9)==0x29B1);
    length=lab_pack(9,LAB_ADC_START,(const uint8_t*)"\x03",1,frame);
    const uint8_t golden[]={0xA5,0x01,0x09,0x10,0x01,0x03,0x08,0x1B};
    assert(length==8);
    assert(memcmp(frame,golden,length)==0);
    assert(frame[0]==LAB_SYNC&&frame[7]==(lab_crc(frame+1,5)&0xff));
    memcpy(bad,frame,length);bad[7]^=0x01;
    for(i=0;i<length;i++) assert(!lab_feed(&parser,bad[i],&request));
    assert(parser.errors==1);
    for(i=0;i<length;i++) got+=lab_feed(&parser,frame[i],&request);
    assert(got==1&&request.seq==9&&request.op==LAB_ADC_START&&request.data[0]==3);
    puts("ATLAS lab C wire-format tests: PASS");
    return 0;
}

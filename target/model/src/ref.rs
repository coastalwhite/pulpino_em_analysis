#![no_main]
#![no_std]

use core::arch::asm;
use core::panic::PanicInfo;

#[panic_handler]
fn panic(_: &PanicInfo) -> ! {
    loop {}
}

#[export_name = "_start"]
fn main() {
    ext_io::led(false);
    ext_io::hal::GpioOut::trigger(false);

    loop {
        ext_io::read();

        ext_io::hal::GpioOut::trigger(true);

        unsafe {
            asm!("
                li      t2,0
                lui     t1,0xFFFFF
                addi    t1,t1,-0x7FF
                {PROLOGUE}
                nop; nop; nop; nop; nop;
                {TRIGGER}
                {TARGET}
                nop; nop; nop; nop; nop;
                {EPILOGUE}
            ", out("t1") _, out("t2") _, out("t3") _, out("t4") _);
        }

        ext_io::hal::GpioOut::trigger(false);
    }
}

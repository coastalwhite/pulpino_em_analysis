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

        flush();

        ext_io::hal::GpioOut::trigger(true);

        unsafe {
            asm!("
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;
                {PROLOGUE}
                nop; nop; nop; nop; nop;
                {TARGET}
                nop; nop; nop; nop; nop;
                {EPILOGUE}
            ",
            out("t0") _,
            out("t1") _,
            out("t2") _,
            out("t3") _,
            out("t4") _,
            out("t5") _,
            out("a1") _,
            out("a4") _,
            out("a5") _,
            out("a6") _,
            out("a7") _,
            out("s2") _,
            out("s3") _,
            );
        }

        ext_io::hal::GpioOut::trigger(false);
    }
}

#[inline(never)]
fn flush() {
    for i in 0..128 {
        unsafe {
            ((0x0010_4000 | (i << 4)) as *const u32).read_volatile();
        }
    }
}

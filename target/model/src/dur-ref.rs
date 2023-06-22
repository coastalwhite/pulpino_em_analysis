#![no_main]
#![no_std]

use core::arch::asm;
use core::panic::PanicInfo;

use ext_io::Timer;

#[panic_handler]
fn panic(_: &PanicInfo) -> ! {
    loop {}
}

#[export_name = "_start"]
fn main() {
    ext_io::led(false);

    flush();

    Timer::reset();
    Timer::start();

    unsafe {
        asm!("
            nop; nop; nop; nop; nop;
            {PROLOGUE}
            nop; nop; nop; nop; nop;
            {TARGET}
            nop; nop; nop; nop; nop;
            {EPILOGUE}
            nop; nop; nop; nop; nop;
        ", 
            out("t0") _,
            out("t1") _,
            out("t2") _,
            out("t3") _,
            out("t4") _,
            out("t5") _,
            out("t6") _,
            out("a0") _,
            out("a1") _,
            out("a2") _,
            out("a3") _,
            out("a4") _,
            out("a5") _,
            out("a6") _,
            out("a7") _,
            out("s2") _,
            out("s3") _,
        );
    }

    Timer::stop();

    ext_io::write_word(Timer::value());
}

#[inline(always)]
fn flush() {
    for i in 0..128 {
        unsafe {
            ((0x0010_4000 | (i << 4)) as *const u32).read_volatile();
        }
    }
}

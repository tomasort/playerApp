#!/bin/bash

dtb_path="/boot/dtbs/6.6.0-odroid-arm64/amlogic/meson64_odroidn2_plus.dtb"

# Convert DTB to DTS
if dtc -q -I dtb -O dts -o ./my_dtb.dts $dtb_path; then
    echo "DTB to DTS conversion successful."
else
    echo "Error: DTB to DTS conversion failed." >&2
    exit 1
fi

# Get the GPIO offset
num2=$(cat /sys/kernel/debug/gpio | grep 'gpiochip0' | awk -F '[ ,:-]+' '{print $3}')
if [ -z "$num2" ]; then
    echo "Error: Failed to get base pin number." >&2
    exit 1
fi

num1=$(cat /sys/kernel/debug/gpio | grep 'PIN_15' | awk '{print $1}' | cut -d '-' -f 2)
if [ -z "$num1" ]; then
    echo "Error: Failed to get GPIO number for pin 15." >&2
    exit 1
fi

result=$((num1 - num2))
offset=$(printf "0x%X\n" $result)
if [ -z "$offset" ]; then
    echo "Error: Failed to calculate GPIO offset." >&2
    exit 1
fi

# Get the phandle
phandle=$(awk -v pinctrl=$(cat /sys/kernel/debug/gpio | grep 'gpiochip0' | awk -F '[ ,:]+' '{print $6}') '{
    if ($0 ~ pinctrl) {
        in_section=1
    }
    if (in_section) {
        if ($0 ~ /bank/) {
            in_bank=1
        }
        if (in_bank && $0 ~ /phandle/) {
            gsub(/[<>;]/, "", $NF)
            print $NF
            exit
        }
        if ($0 ~ /};/) {
            in_section=0
        }
    }
}' my_dtb.dts)

if [ -z "$phandle" ]; then
    echo "Error: Failed to get phandle." >&2
    exit 1
fi

# Print the result
echo "Offset: $offset"
echo "Phandle: $phandle"

# Modify the DTB file
if fdtput -v -c $dtb_path /ir-tx; then
    echo "Node /ir-tx created successfully."
else
    echo "Error: Failed to create node /ir-tx." >&2
    exit 1
fi

if fdtput -t s $dtb_path /ir-tx compatible "gpio-ir-tx"; then
    echo "Compatible property set successfully."
else
    echo "Error: Failed to set compatible property." >&2
    exit 1
fi

if fdtput -t x $dtb_path /ir-tx "gpios" $phandle $offset 0x00; then
    echo "GPIOs property set successfully."
else
    echo "Error: Failed to set GPIOs property. phandle:$phandle, offset:$offset" >&2
    exit 1
fi

# Delete the DTS file
if rm my_dtb.dts; then
    echo "Temporary DTS file deleted."
else
    echo "Error: Failed to delete temporary DTS file." >&2
    exit 1
fi

# Prompt for reboot
read -p "Would you like to reboot the system now? (yes/no): " response
if [[ "$response" == "yes" || "$response" == "y" ]]; then
    echo "Rebooting the system..."
    sudo reboot
else
    echo "Please reboot the system whenever convenient."
fi

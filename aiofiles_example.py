import asyncio
import aiofiles

async def main():
    """
    This example demonstrates the basic usage of aiofiles to asynchronously
    write to and read from a file.
    """
    # Define the filename
    filename = "test_aiofile.txt"

    # Asynchronously write to a file
    try:
        async with aiofiles.open(filename, mode='w') as f:
            await f.write("Hello, aiofiles!\n")
            await f.write("This is an asynchronous file operation.\n")
        print(f"Successfully wrote to {filename}")
    except Exception as e:
        print(f"Error writing to file: {e}")

    # Asynchronously read from the file
    try:
        async with aiofiles.open(filename, mode='r') as f:
            print(f"\nReading from {filename}:")
            content = await f.read()
            print(content)
    except Exception as e:
        print(f"Error reading from file: {e}")

if __name__ == "__main__":
    # To run an async function, you use asyncio.run()
    asyncio.run(main())


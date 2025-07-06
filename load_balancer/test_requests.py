import aiohttp
import asyncio
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_request(session, url, semaphore, max_retries=3):
    for attempt in range(max_retries):
        async with semaphore:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("server", data.get("message", "").split(": ")[1] if "Hello from Server" in data.get("message", "") else None)
                    return None
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(1)  # Wait before retry



async def test_load_distribution(n_servers=3, num_requests=10000, concurrency=100):
    logger.info(f"Testing load distribution with N={n_servers}, {num_requests} requests")
    semaphore = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency)

    async def safe_send(session):
        return await send_request(session, "http://localhost:5000/home", semaphore)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [safe_send(session) for _ in range(num_requests)]
            responses = await asyncio.gather(*tasks)
            successful = [r for r in responses if r is not None]
            server_counts = Counter(successful)
            failed_count = num_requests - len(successful)
            logger.info(f"Server counts: {server_counts}")
            logger.warning(f"{failed_count} requests failed out of {num_requests}")

            if server_counts:
                plt.figure(figsize=(8, 6))
                sns.barplot(x=list(server_counts.keys()), y=list(server_counts.values()))
                plt.xlabel("Server Instances")
                plt.ylabel("Number of Requests")
                plt.title(f"Load Distribution for {num_requests} Requests (N={n_servers})")
                plt.savefig("load_distribution.png")
                plt.close()
            else:
                logger.error("No valid responses received")
            return server_counts
    except Exception as e:
        logger.error(f"Load distribution test failed: {e}")
        return {}

async def test_scalability():
    results = []
    async with aiohttp.ClientSession() as session:
        for n in range(2, 7):
            logger.info(f"Testing scalability with N={n}")
            try:
                async with session.get("http://localhost:5000/rep") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        current = data["message"]["N"]
                    else:
                        current = 0
                if n > current:
                    await session.post("http://localhost:5000/add", json={"n": n - current, "hostnames": [f"server{i}" for i in range(current + 1, n + 1)]})
                elif n < current:
                    await session.delete("http://localhost:5000/rm", json={"n": current - n})
                counts = await test_load_distribution(n_servers=n, num_requests=10000, concurrency=100)
                avg_load = sum(counts.values()) / n if counts else 0
                results.append((n, avg_load))
            except Exception as e:
                logger.error(f"Scalability test for N={n} failed: {e}")
                results.append((n, 0))

    if results:
        plt.figure(figsize=(8, 6))
        sns.lineplot(x=[r[0] for r in results], y=[r[1] for r in results], marker='o')
        plt.xlabel("Number of Servers (N)")
        plt.ylabel("Average Load (Requests per Server)")
        plt.title("Scalability Analysis (N=2 to 6)")
        plt.savefig("scalability.png")
        plt.close()
    return results

if __name__ == "__main__":
    try:
        asyncio.run(test_load_distribution())  # A-1


        asyncio.run(test_scalability())        # A-2


    except Exception as e:
        logger.error(f"Test failed: {e}")

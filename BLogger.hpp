#pragma once
#include <fstream>
#include <mutex>

enum class LogLevel { All, Debug, Info, Warning, Error, Critical };

#ifdef NDEBUG
constexpr LogLevel Blogger_default_mask = LogLevel::Debug;
constexpr LogLevel Blogger_minimum_loglovel = LogLevel::Info;
#else
constexpr LogLevel Blogger_default_mask = LogLevel::All;
constexpr LogLevel Blogger_minimum_loglovel = LogLevel::Debug;
#endif // _DEBUG


#ifdef _WIN32
const char* std_out = "CON";
const char* std_err = "CON";
#elif defined(__linux__)
const char* std_out = "/dev/stdout";
const char* std_err = "/dev/stderr";
#endif 

class BLogger;

class BLoggerStream
{
	friend class BLogger;
private:
	inline BLoggerStream(BLogger& logger, LogLevel lv);
	BLogger& logger;
	LogLevel lv;
	std::ofstream& stream;
public:
	template <typename T>
	BLoggerStream& operator<<(const T& info);
	inline ~BLoggerStream();
};

class BLogger
{
public:
	friend class BLoggerStream;
private:
	std::ofstream basic_logout;
	std::ofstream error_logout;
	std::mutex mtx;
	LogLevel mask;
	bool use_ms;

	const char* logTime() {
		using namespace std::chrono;
		time_t t = system_clock::to_time_t(time_point_cast<microseconds>(system_clock::now()));
		char* s = ctime(&t);
		s[24] = 0;
		return s;
	}

	void logTime(char* buffer, bool use_ms)
	{
		using namespace std::chrono;
		auto time = time_point_cast<milliseconds>(system_clock::now());
		time_t t = system_clock::to_time_t(time);
		if (use_ms)
		{
			strftime(buffer, 32, "%a %b %d %X.000000 %Y", localtime(&t));
			int millisecond = time.time_since_epoch().count() % 1000000;
			for (int i = 0; i < 6; i++)
			{
				buffer[25 - i] = millisecond % 10 + '0';
				millisecond /= 10;
			}
			buffer[26] = ' ';
		}
		else 
			strftime(buffer, 32, "%c", localtime(&t));
	}
	
	std::ofstream& basicLog(LogLevel lv) {
		{		

			const char* level = "";
			std::ofstream* stream = &basic_logout;
			if (lv <= mask)
				return *stream;
			switch (lv)
			{
			case LogLevel::Debug:
				level = "[Debug]:";
				break;
			case LogLevel::Info:
				level = "[Info]:";
				break;
			case LogLevel::Warning:
				level = "[Warning]:";
				break;
			case LogLevel::Error:
				level = "[Error]:";
				stream = &error_logout;
				break;
			case LogLevel::Critical:
				level = "[Critical]:";
				stream = &error_logout;
				break;
			default:
				break;
			}
			char timeBuffer[32];
			logTime(timeBuffer, use_ms);
			*stream << timeBuffer << " " << level << " ";
			return *stream;
		}
	}
public:
	BLogger(LogLevel mask = Blogger_default_mask,bool use_ms = false,const char* fout = std_out, const char* ferr = std_err)
		:mask(mask), basic_logout(fout), error_logout(ferr),use_ms(use_ms)
	{
		basic_logout.sync_with_stdio(false);
		error_logout.sync_with_stdio(false);
	}
	
	void log(LogLevel lv, const char* description) {

		mtx.lock();
		basicLog(lv) << description << std::endl;
		mtx.unlock();
	}
	
	BLoggerStream operator()(LogLevel lv = LogLevel::Debug) {
		mtx.lock();
		return BLoggerStream(*this,lv);
	}
	template <typename T>
	BLoggerStream operator<<(const T& info) {
		mtx.lock();
		BLoggerStream ret(*this, LogLevel::Debug);
		ret << info;
		return ret;
	}
};

BLoggerStream::BLoggerStream(BLogger& logger, LogLevel lv)
	:logger(logger), lv(lv), stream(logger.basicLog(lv))
{
}

BLoggerStream::~BLoggerStream()
{
	if (lv > logger.mask)
		stream << std::endl;
	logger.mtx.unlock();
}

template <typename T>
BLoggerStream& BLoggerStream::operator<<(const T& info) {
	if (lv > logger.mask)
		stream << info;
	return *this;
}